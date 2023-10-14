all: buildmo

buildmo:
	@echo "Building the mo files"
	mkdir -p usr/share/locale/ko/LC_MESSAGES
	if [ -f po/mintupdate-ko.po ]; then \
		msgfmt -o usr/share/locale/ko/LC_MESSAGES/mintupdate.mo po/mintupdate-ko.po; \
	fi
	if [ -f po/synaptic-ko.po ]; then \
		msgfmt -o usr/share/locale/ko/LC_MESSAGES/synaptic.mo po/synaptic-ko.po; \
	fi

clean:
	rm -rf usr/share/locale
